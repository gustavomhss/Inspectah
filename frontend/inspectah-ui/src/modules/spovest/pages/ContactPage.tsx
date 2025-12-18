import { useState } from 'react';
import { Link } from 'react-router-dom';
import { SpButton } from '../components/ui/Button';
import { SpInput, SpTextarea, SpCheckbox } from '../components/ui/Input';
import { SpCard } from '../components/ui/Card';

const contactInfo = [
  {
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    label: 'Email',
    value: 'support@spovest.com',
    href: 'mailto:support@spovest.com',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
      </svg>
    ),
    label: 'Phone',
    value: '+1 (987) 664-32-11',
    href: 'tel:+19876643211',
  },
  {
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    label: 'Address',
    value: '4293 Euclid Avenue, Los Angeles, CA 90012',
    href: 'https://maps.google.com',
  },
];

export function SpContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
    acceptMarketing: false,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500));

    setIsSubmitting(false);
    setIsSubmitted(true);
  };

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-900/30 via-slate-900 to-cyan-900/20" />
        <div className="absolute top-10 right-20 w-72 h-72 bg-cyan-600/20 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-sm text-slate-400 mb-8">
            <Link to="/spovest" className="hover:text-white transition-colors">Home</Link>
            <span>/</span>
            <span className="text-white">Contact Us</span>
          </nav>

          <div className="max-w-3xl">
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6">
              Get in{' '}
              <span className="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
                Touch
              </span>
            </h1>
            <p className="text-xl text-slate-300">
              Have a question or feedback? We'd love to hear from you. Check out our{' '}
              <Link to="/spovest/faq" className="text-violet-400 hover:underline">FAQ</Link>{' '}
              first, or send us a message below.
            </p>
          </div>
        </div>
      </section>

      {/* Contact Info Cards */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-6">
            {contactInfo.map((info) => (
              <a
                key={info.label}
                href={info.href}
                target={info.label === 'Address' ? '_blank' : undefined}
                rel={info.label === 'Address' ? 'noopener noreferrer' : undefined}
                className="block"
              >
                <SpCard variant="bordered" hover className="text-center h-full">
                  <div className="w-14 h-14 rounded-full bg-violet-600/20 flex items-center justify-center mx-auto mb-4 text-violet-400">
                    {info.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{info.label}</h3>
                  <p className="text-slate-400">{info.value}</p>
                </SpCard>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Form */}
      <section className="py-16">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <SpCard variant="gradient">
            <h2 className="text-2xl font-bold text-white mb-2 text-center">
              We'd Love to Hear from You
            </h2>
            <p className="text-slate-400 text-center mb-8">
              Fill out the form below and we'll get back to you within 24 hours.
            </p>

            {isSubmitted ? (
              <div className="text-center py-12">
                <div className="w-20 h-20 rounded-full bg-emerald-600/20 flex items-center justify-center mx-auto mb-6">
                  <svg className="w-10 h-10 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Message Sent!</h3>
                <p className="text-slate-400 mb-6">
                  Thank you for reaching out. We'll get back to you soon.
                </p>
                <SpButton variant="outline" onClick={() => setIsSubmitted(false)}>
                  Send Another Message
                </SpButton>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid sm:grid-cols-2 gap-6">
                  <SpInput
                    label="Full Name"
                    name="name"
                    placeholder="John Doe"
                    value={formData.name}
                    onChange={handleChange}
                    required
                  />
                  <SpInput
                    label="Email Address"
                    type="email"
                    name="email"
                    placeholder="john@example.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </div>

                <SpInput
                  label="Subject"
                  name="subject"
                  placeholder="How can we help?"
                  value={formData.subject}
                  onChange={handleChange}
                  required
                />

                <SpTextarea
                  label="Message"
                  name="message"
                  placeholder="Tell us more about your inquiry..."
                  rows={6}
                  value={formData.message}
                  onChange={handleChange}
                  required
                />

                <SpCheckbox
                  name="acceptMarketing"
                  label="I agree to receive emails, newsletters, and promotional messages from Spovest"
                  checked={formData.acceptMarketing}
                  onChange={handleChange}
                />

                <SpButton type="submit" size="lg" fullWidth loading={isSubmitting}>
                  Send Message
                </SpButton>
              </form>
            )}
          </SpCard>
        </div>
      </section>

      {/* Map Placeholder */}
      <section className="py-16 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-slate-800/50 rounded-2xl h-96 border border-slate-700/50 flex items-center justify-center">
            <div className="text-center">
              <svg className="w-16 h-16 text-slate-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              <p className="text-slate-500">Interactive Map</p>
              <p className="text-slate-600 text-sm mt-2">4293 Euclid Avenue, Los Angeles, CA</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
